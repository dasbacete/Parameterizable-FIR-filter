library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;
use IEEE.MATH_REAL.ALL;
use STD.ENV.FINISH;

entity tb_fir is
end entity tb_fir;

architecture test of tb_fir is

	-- components
	component FIR is
		generic(
			WGTW: integer := 8;
			DW:   integer := 16;
			N_SG: integer := 4;
			constant WAW: integer;
			constant OW:  integer);
		Port(
			clk:      in  std_logic;
			rst:      in  std_logic;
			stb_in:   in  std_logic;
			calc:     in  std_logic;
			bsy_in:   in  std_logic;
			data_in:  in  signed (DW-1 downto 0);
			wgt_addr: in 	unsigned (WAW-1 downto 0);
			wgt_in:   in  signed (WGTW-1 downto 0);
			stb_out:  out std_logic;
			bsy_out:  out std_logic;
			data_out: out signed (OW-1 downto 0));
	end component;

	-- constants
	constant W_FILE:            string  := "/home/happybug/wdir/fir/prj/io/weights.txt";
	constant I_FILE:            string  := "/home/happybug/wdir/fir/prj/io/input.txt";
	constant O_FILE:            string  := "/home/happybug/wdir/fir/prj/io/output_dut.txt";
	constant NUMBER_OF_STAGES:  integer := 32;
	constant DATA_WIDTH:        integer := 16;
	constant WEIGHT_WIDTH:      integer := 12;
	constant OUTPUT_DATA_WIDTH: integer := integer(ceil(log2(real(NUMBER_OF_STAGES)))) + DATA_WIDTH + WEIGHT_WIDTH;
	constant W_ADDR_WIDTH:      integer := integer(ceil(log2(real(NUMBER_OF_STAGES))));
  constant CLOCK_PERIOD:      time    := 10 ns;
  constant RESET_STOP:        time    := 40 ns;

	-- signals
	signal clk, calc:       	 	 std_logic := '0';
	signal rst:             	 	 std_logic := '1';
	signal w_addr, w_addr_n: 		 unsigned (W_ADDR_WIDTH-1 downto 0) := (others=>'0');
	signal ctrl_cnt, ctrl_cnt_n: integer;

	signal bsy_out, stb_out:     std_logic;
	signal bsy_in, stb_in:       std_logic;
	signal weight:               signed (WEIGHT_WIDTH-1 downto 0);
	signal data_out:             signed (OUTPUT_DATA_WIDTH-1 downto 0);
	signal data_in:              signed (DATA_WIDTH-1 downto 0);

	-- other
	file weights : text;
	file input   : text;
	file output  : text;

begin

	-- ctrl

	rst <= '0' after RESET_STOP;
	clk <= not clk after CLOCK_PERIOD / 2;
	process(clk)
	begin
		if rising_edge(clk) then
			if (rst='1') then
				ctrl_cnt <= 0;
			else
				ctrl_cnt <= ctrl_cnt_n;
			end if;
		end if;
	end process;

	process(ctrl_cnt)
	begin
		ctrl_cnt_n <= ctrl_cnt + 1;
	end process;

	-- functionality
	process
		file     fp:           text;
		variable fstatus:      file_open_status;
		variable wc:           bit_vector(WEIGHT_WIDTH-1 downto 0);
		variable idc:          bit_vector(DATA_WIDTH-1 downto 0);
		variable weight_data:  std_logic_vector(WEIGHT_WIDTH-1 downto 0);
		variable input_data:   std_logic_vector(DATA_WIDTH-1 downto 0);
    variable line_num:     line;
	begin
		-- Load weights
		stb_in <= '0';
		bsy_in <= '0';
		calc <= '0';
		w_addr <= (others=>'0');
		file_open(fstatus, fp, W_FILE, READ_MODE);
		wait until rst='0';
		while(not endfile(fp)) loop
			readline(fp, line_num);
      read(line_num, wc);
      weight_data := to_stdlogicvector(wc);
      weight <= signed(weight_data);
			wait until rising_edge(clk);
			w_addr <= w_addr + 1;
		end loop;
		file_close(fp);
		-- input
		calc <= '1';
		stb_in <= '1';
		file_open(fstatus, fp, I_FILE, READ_MODE);
		while(not endfile(fp)) loop
			readline(fp, line_num);
      read(line_num, idc);
      input_data := to_stdlogicvector(idc);
      data_in <= signed(input_data);
			wait until rising_edge(clk);
		end loop;
		file_close(fp);
		calc <= '0';
	end process;

	-- write output
	process
		file 		 fw: 				text;
		variable fstatus_w: file_open_status;
		variable wdc:       bit_vector(OUTPUT_DATA_WIDTH-1 downto 0);
		variable out_line:  line;
		variable dout:      std_logic_vector(OUTPUT_DATA_WIDTH-1 downto 0);
	begin
		wait until rst = '0';
		file_open(fstatus_w, fw, O_FILE, WRITE_MODE);
		wait until calc='1';
		while (calc='1') loop
			wait until rising_edge(clk);
			if stb_out='1' then
				 dout := std_logic_vector(data_out);
			   wdc := to_bitvector(dout);
				 write(out_line, wdc);
				 write(out_line, LF);
			end if;
		end loop;
		writeline(fw, out_line);
		file_close(fw);
		FINISH(0);
	end process;
	--DUT
	DUT : FIR
		Generic map (
			WGTW => WEIGHT_WIDTH,
			DW   => DATA_WIDTH,
			N_SG => NUMBER_OF_STAGES,
	 		WAW  => integer(ceil(log2(real(NUMBER_OF_STAGES)))),
			OW   => integer(ceil(log2(real(NUMBER_OF_STAGES)))) + DATA_WIDTH + WEIGHT_WIDTH)
		Port map (
			clk      => clk,
			rst      => rst,
			stb_in   => stb_in,
			calc     => calc,
			bsy_in   => bsy_in,
			data_in  => data_in,
			wgt_addr => w_addr,
			wgt_in   => weight,
			stb_out  => stb_out,
			bsy_out  => bsy_out,
			data_out => data_out );

end test;
