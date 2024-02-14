library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity SG is
	generic (
		DW:     integer := 16;
		SW_IN:  integer := 16;
		SW_OUT: integer := 16;
		WGTW:   integer := 8);
	Port(
		clk:     in std_logic;
		rst:     in std_logic;
		stb_in:  in std_logic;
		bsy_in:  in std_logic;
		sum_in:  in signed (SW_IN-1 downto 0);
		wgt:     in signed (WGTW-1 downto 0);
		dly_in:  in signed (DW-1 downto 0);
		stb_out: out std_logic;
		dly_out: out signed (DW-1 downto 0);
		sum_out: out signed (SW_OUT-1 downto 0));
end SG;
architecture Behavioral of SG is

	signal dly_sig: signed (DW-1 downto 0);

begin

	-- Data signals
	dly_out <= dly_sig;
	sum_out <= resize(sum_in + (dly_sig * wgt), sum_out'length);

	-- Delay
	process (clk)
	begin
		if rising_edge(clk) then
			if rst = '1' then
				stb_out <= '0';
				dly_sig <= ( others => '0');
			else
				stb_out <= stb_in;
				if (bsy_in = '0') and (stb_in = '1') then
					dly_sig <= dly_in;
				end if;
			end if;
		end if;
	end process;

end Behavioral;
